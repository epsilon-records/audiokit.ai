/* CONFIDENTIAL AND PROPRIETARY
 * 
 * Copyright (c) 2025 AudioKit.ai. All rights reserved.
 * 
 * This software is confidential and proprietary.
 */

* 
 * This software is confidential and proprietary.
 */

interface FAQCategory {
  title: string;
  questions: {
    question: string;
    answer: string;
  }[];
}

export type FAQData = FAQCategory[];
