interface FAQCategory {
  title: string;
  questions: {
    question: string;
    answer: string;
  }[];
}

export type FAQData = FAQCategory[];
