import { parse, Parser } from 'csv-parse';
import { createReadStream } from 'fs';
import Bottleneck from 'bottleneck';

// Types
interface Config {
    csvPath: string;
    pbUrl: string;
    collection: string;
}

interface DelimiterCount {
    char: string;
    count: number;
}

type CSVRecord = Record<string, string>;

interface PocketBaseRecord {
    id: string;
    [key: string]: any;
}

// Constants
const RATE_LIMIT = {
    maxConcurrent: 1,
    minTime: 1000,
} as const;

const DELIMITERS = {
    COMMA: ',',
    SEMICOLON: ';',
    TAB: '\t',
} as const;

// Add new interface for tracking statistics
interface ProcessingStats {
    processed: number;
    created: number;
    updated: number;
    errors: number;
    skipped: number;
}

// Utility functions
async function readFileContent(filePath: string): Promise<string> {
    return new Promise((resolve, reject) => {
        const chunks: Buffer[] = [];
        const readStream = createReadStream(filePath);
        
        readStream.on('data', (chunk) => chunks.push(Buffer.from(chunk)));
        readStream.on('error', (error) => reject(error));
        readStream.on('end', () => resolve(Buffer.concat(chunks).toString('utf8')));
    });
}

function countDelimiter(text: string, delimiter: string): number {
    return (text.match(new RegExp(delimiter === '\t' ? '\t' : `\\${delimiter}`, 'g')) || []).length;
}

function detectDelimiter(firstLine: string): string {
    const counts: DelimiterCount[] = [
        { char: DELIMITERS.COMMA, count: countDelimiter(firstLine, DELIMITERS.COMMA) },
        { char: DELIMITERS.SEMICOLON, count: countDelimiter(firstLine, DELIMITERS.SEMICOLON) },
        { char: DELIMITERS.TAB, count: countDelimiter(firstLine, DELIMITERS.TAB) },
    ];

    const mostFrequent = counts.reduce((prev, current) => 
        current.count > prev.count ? current : prev
    );

    return mostFrequent.char;
}

function cleanUrl(url: string): string {
    if (!url) return url;
    
    // Remove www if present
    let cleanedUrl = url.replace(/^(?:https?:\/\/)?(?:www\.)?/i, '');
    
    // Ensure https:// protocol
    return `https://${cleanedUrl}`;
}

// PocketBase API Client
class PocketBaseClient {
    private readonly baseUrl: string;
    private readonly collection: string;
    private readonly limiter: Bottleneck;
    private stats: ProcessingStats = {
        processed: 0,
        created: 0,
        updated: 0,
        errors: 0,
        skipped: 0
    };

    constructor(pbUrl: string, collection: string) {
        this.baseUrl = pbUrl.endsWith('/') ? pbUrl.slice(0, -1) : pbUrl;
        this.collection = collection;
        this.limiter = new Bottleneck(RATE_LIMIT);
        
        // Add debug events
        this.limiter.on('received', () => console.log('Task received by limiter'));
        this.limiter.on('queued', () => console.log('Task queued'));
        this.limiter.on('executing', () => console.log('Task executing'));
        this.limiter.on('done', () => console.log('Task completed'));
    }

    getStats(): ProcessingStats {
        return this.stats;
    }

    private async findRecordByStageName(stageName: string): Promise<PocketBaseRecord | null> {
        const url = `${this.baseUrl}/api/collections/${this.collection}/records?filter=(stage_name='${encodeURIComponent(stageName)}')`;
        const response = await fetch(url);

        if (!response.ok) {
            throw new Error(`Failed to search for record: ${await response.text()}`);
        }

        const data = await response.json();
        return data.items.length > 0 ? data.items[0] : null;
    }

    async processRecord(record: CSVRecord, rowNumber: number): Promise<void> {
        return this.limiter.schedule(async () => {
            try {
                this.stats.processed++;
                
                // Clean URLs in the record
                const cleanedRecord = { ...record };
                const urlFields = [
                    'website',
                    'spotify',
                    'apple_music',
                    'bandcamp',
                    'mixcloud',
                    'snapchat',
                    'twitch',
                    'youtube',
                    'instagram',
                    'facebook',
                    'x',           
                    'tiktok',
                    'soundcloud',
                    'songkick',
                    'bandsintown',
                    'linkedin'
                ];
                
                for (const field of urlFields) {
                    if (cleanedRecord[field]) {
                        cleanedRecord[field] = cleanUrl(cleanedRecord[field]);
                    }
                }

                console.log(`Row ${rowNumber}: Processing record:`, cleanedRecord);

                if (!cleanedRecord.stage_name) {
                    console.error(`Row ${rowNumber}: Error - stage_name is required but missing`);
                    this.stats.errors++;
                    return;
                }

                // Check for existing record
                try {
                    const existingRecord = await this.findRecordByStageName(cleanedRecord.stage_name);
                    const url = `${this.baseUrl}/api/collections/${this.collection}/records${existingRecord ? `/${existingRecord.id}` : ''}`;
                    
                    const response = await fetch(url, {
                        method: existingRecord ? 'PATCH' : 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify(cleanedRecord)
                    });
                    
                    if (!response.ok) {
                        const errorText = await response.text();
                        throw new Error(`API Error: ${errorText}`);
                    }

                    if (existingRecord) {
                        this.stats.updated++;
                        console.log(`Row ${rowNumber}: Updated record for ${cleanedRecord.stage_name}`);
                    } else {
                        this.stats.created++;
                        console.log(`Row ${rowNumber}: Created record for ${cleanedRecord.stage_name}`);
                    }

                } catch (error) {
                    console.error(`Row ${rowNumber}: Error - ${error}`);
                    this.stats.errors++;
                }
            } catch (error) {
                console.error(`Row ${rowNumber}: Error - ${error}`);
                this.stats.errors++;
            }
        });
    }
}

// CSV Parser
class CSVParser {
    private readonly filePath: string;
    private readonly pbClient: PocketBaseClient;

    constructor(filePath: string, pbClient: PocketBaseClient) {
        this.filePath = filePath;
        this.pbClient = pbClient;
    }

    private createParser(delimiter: string): Parser {
        return parse({
            columns: (headers: string[]) => {
                const trimmedHeaders = headers.map(header => header?.trim() || '');
                
                const emptyHeaders = trimmedHeaders.filter(header => !header);
                if (emptyHeaders.length > 0) {
                    throw new Error('Empty or invalid headers found in CSV');
                }
                
                console.log('\nCSV Headers:', trimmedHeaders);
                return trimmedHeaders;
            },
            skip_empty_lines: true,
            trim: true,
            skip_records_with_error: false,
            delimiter,
            quote: '"',
            escape: '"',
            relax_quotes: true,
            from_line: 1
        });
    }

    async parse(): Promise<void> {
        const fileContent = await readFileContent(this.filePath);
        const firstLine = fileContent.split('\n')[0];
        const delimiter = detectDelimiter(firstLine);
        
        console.log(`Detected delimiter: "${delimiter}"`);

        const parser = this.createParser(delimiter);
        const processPromises: Promise<void>[] = [];
        let recordCount = 0;
        let skipCount = 0;

        return new Promise((resolve, reject) => {
            parser.on('readable', () => {
                let record: CSVRecord;
                while ((record = parser.read()) !== null) {
                    recordCount++;
                    processPromises.push(this.pbClient.processRecord(record, recordCount));
                }
            });

            parser.on('skip', (error) => {
                skipCount++;
                (this.pbClient as PocketBaseClient).getStats().skipped++;
                console.warn(`Skipped line ${skipCount} due to error:`, error.message);
            });

            parser.on('error', reject);

            parser.on('end', async () => {
                console.log(`\nParser finished.`);
                console.log(`Records found: ${recordCount}`);
                console.log(`Records skipped: ${skipCount}`);

                try {
                    await Promise.all(processPromises);
                    const stats = (this.pbClient as PocketBaseClient).getStats();
                    console.log('\nProcessing Summary:');
                    console.log(`Total Processed: ${stats.processed}`);
                    console.log(`Created: ${stats.created}`);
                    console.log(`Updated: ${stats.updated}`);
                    console.log(`Errors: ${stats.errors}`);
                    console.log(`Skipped: ${stats.skipped}`);
                    resolve();
                } catch (error) {
                    reject(error);
                }
            });

            createReadStream(this.filePath).pipe(parser);
        });
    }
}

// Main execution
async function main() {
    try {
        const args = process.argv.slice(2);

        if (args.length !== 3) {
            throw new Error('Usage: script.ts <csv-path> <pb-url> <collection>');
        }

        const config: Config = {
            csvPath: args[0],
            pbUrl: args[1],
            collection: args[2]
        };

        const pbClient = new PocketBaseClient(config.pbUrl, config.collection);
        const csvParser = new CSVParser(config.csvPath, pbClient);
        
        await csvParser.parse();
        console.log('Script completed successfully');
        process.exit(0);
    } catch (error) {
        console.error('Script failed:', error);
        process.exit(1);
    }
}

// Execute
main();

export { PocketBaseClient, CSVParser };