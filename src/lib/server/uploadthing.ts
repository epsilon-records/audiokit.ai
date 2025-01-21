import { createUploadthing, type FileRouter } from 'uploadthing/server';
import { auth } from './auth';

const f = createUploadthing();

export const uploadRouter = {
  // Define image upload endpoints
  imageUploader: f({ image: { maxFileSize: '4MB', maxFileCount: 1 } })
    .middleware(async ({ req }) => {
      const session = await auth(req);
      if (!session) throw new Error('Unauthorized');
      return { userId: session.userId };
    })
    .onUploadComplete(async ({ metadata, file }) => {
      return { fileUrl: file.url };
    }),

  // Define audio upload endpoints
  audioUploader: f({ audio: { maxFileSize: '256MB', maxFileCount: 1 } })
    .middleware(async ({ req }) => {
      const session = await auth(req);
      if (!session) throw new Error('Unauthorized');
      return { userId: session.userId };
    })
    .onUploadComplete(async ({ metadata, file }) => {
      return { fileUrl: file.url };
    }),

  // Define document upload endpoints (for contracts etc)
  documentUploader: f({
    pdf: { maxFileSize: '8MB', maxFileCount: 1 },
    text: { maxFileSize: '8MB', maxFileCount: 1 },
  })
    .middleware(async ({ req }) => {
      const session = await auth(req);
      if (!session) throw new Error('Unauthorized');
      return { userId: session.userId };
    })
    .onUploadComplete(async ({ metadata, file }) => {
      return { fileUrl: file.url };
    }),
} satisfies FileRouter;

export type OurFileRouter = typeof uploadRouter;
