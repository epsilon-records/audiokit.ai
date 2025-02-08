/* CONFIDENTIAL AND PROPRIETARY
 * 
 * Copyright (c) 2025 AudioKit.ai. All rights reserved.
 * 
 * This software is confidential and proprietary.
 */

* 
 * This software is confidential and proprietary.
 */

export default {
  '**/*.ts': () => 'tsc --noEmit',
  '**/*.{ts,js,md,svelte,css,html,json}': ['eslint --fix', 'prettier --write --list-different'],
};
