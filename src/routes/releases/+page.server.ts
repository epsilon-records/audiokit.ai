import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async () => {
  try {
    const releases = null;

    return {
      releases: releases,
    };
  } catch (err) {
    return {
      releases: [],
    };
  }
};
