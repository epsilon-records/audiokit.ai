import { parse, Parser } from 'csv-parse';
import { createReadStream } from 'fs';
import Bottleneck from 'bottleneck';

// Types
interface Config {
    csvPath: string;
    pbUrl: string;
    collection: string;
    token: string;
}

interface DelimiterCount {
    char: string;
    count: number;
}

type CSVRecord = Record<string, string>;

// Constants
const RATE_LIMIT = {
    maxConcurrent: 50,
    minTime: 200,
} as const;

const DELIMITERS = {
    COMMA: ',',
    SEMICOLON: ';',
    TAB: '\t',
} as const;

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

// PocketBase API Client
class PocketBaseClient {
    private readonly baseUrl: string;
    private readonly collection: string;
    private readonly token: string;
    private readonly limiter: Bottleneck;

    constructor(pbUrl: string, collection: string, token: string) {
        this.baseUrl = pbUrl.endsWith('/') ? pbUrl.slice(0, -1) : pbUrl;
        this.collection = collection;
        this.token = token;
        this.limiter = new Bottleneck(RATE_LIMIT);
    }

    async createRecord(record: CSVRecord): Promise<void> {
        const filteredRecord = Object.fromEntries(
            Object.entries(record).filter(([key]) => /^[a-z]/.test(key))
        );

        if (Object.keys(filteredRecord).length === 0) {
            throw new Error('No valid fields found after filtering');
        }

        const url = `${this.baseUrl}/api/collections/${this.collection}/records`;
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${this.token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(filteredRecord)
        });

        if (!response.ok) {
            const error = await response.text();
            throw new Error(`API Error: ${error}`);
        }
    }

    async processRecord(record: CSVRecord, rowNumber: number): Promise<void> {
        return this.limiter.schedule(async () => {
            try {
                console.log(`Row ${rowNumber}: Processing record:`, record);
                
                const filteredRecord = Object.fromEntries(
                    Object.entries(record).filter(([key]) => /^[a-z]/.test(key))
                );

                if (Object.keys(filteredRecord).length === 0) {
                    console.warn(`Row ${rowNumber}: Skipped - No valid fields found after filtering`);
                    return;
                }

                const url = `${this.baseUrl}/api/collections/${this.collection}/records`;
                const response = await fetch(url, {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${this.token}`,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(filteredRecord)
                });

                if (!response.ok) {
                    const error = await response.text();
                    console.error(`Row ${rowNumber}: API Error - ${error}. Skipping record.`);
                    return;
                }

                console.log(`Row ${rowNumber}: Success`);
            } catch (error) {
                console.error(`Row ${rowNumber}: Error - ${error}. Skipping record.`);
                return;
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
                console.log('\nAll headers found:', headers);
                return headers.map(header => header?.trim() || '');
            },
            skip_empty_lines: true,
            trim: true,
            skip_records_with_error: true,
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
                console.warn(`Skipped line ${skipCount} due to error:`, error.message);
            });

            parser.on('error', reject);

            parser.on('end', async () => {
                console.log(`\nParser finished.`);
                console.log(`Records found: ${recordCount}`);
                console.log(`Records skipped: ${skipCount}`);

                try {
                    await Promise.all(processPromises);
                    console.log('All processing completed');
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

        if (args.length !== 4) {
            throw new Error('Usage: script.ts <csv-path> <pb-url> <collection> <token>');
        }

        const config: Config = {
            csvPath: args[0],
            pbUrl: args[1],
            collection: args[2],
            token: args[3]
        };

        const pbClient = new PocketBaseClient(config.pbUrl, config.collection, config.token);
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