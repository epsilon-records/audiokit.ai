declare module 'typewriter-effect/dist/core' {
  export default class Typewriter {
    constructor(
      element: HTMLElement,
      options?: {
        delay: number;
        cursor: string;
        cursorClassName?: string;
      }
    );

    typeString(str: string): this;
    deleteChars(count: number): this;
    pauseFor(ms: number): this;
    start(): this;
    stop(): void;
  }
}
