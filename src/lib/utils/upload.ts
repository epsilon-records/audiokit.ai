import { createUploadThing } from '$lib/utils/uploadthing';

const { uploadFiles, uploadComplete } = createUploadThing();

export async function uploadFile(
  file: File,
  type: 'image' | 'audio' | 'document'
): Promise<string> {
  try {
    const endpoint = `${type}Uploader`;
    const res = await uploadFiles([file], endpoint);

    if (!res[0].url) {
      throw new Error('Upload failed');
    }

    return res[0].url;
  } catch (err) {
    console.error('Upload error:', err);
    throw new Error('Failed to upload file');
  }
}

export function getFileUrl(url: string): string {
  return url;
}
