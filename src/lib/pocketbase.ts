import PocketBase from 'pocketbase';
import { PUBLIC_POCKETBASE_URL } from '$env/static/public';
import { PB_SECRET_KEY } from '$env/static/private';

export const pb = new PocketBase(PUBLIC_POCKETBASE_URL)
await pb.collection("users").authWithPassword('pb@epsilonrecords.com', PB_SECRET_KEY);