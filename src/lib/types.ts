import type { z } from 'zod';
import type { artistSchema } from './schemas/artist';

export type Artist = z.infer<typeof artistSchema>;