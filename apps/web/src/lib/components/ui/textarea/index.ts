/* CONFIDENTIAL AND PROPRIETARY
 * 
 * Copyright (c) 2025 AudioKit.ai. All rights reserved.
 * 
 * This software is confidential and proprietary.
 */

* 
 * This software is confidential and proprietary.
 */

import Root from './textarea.svelte';

type FormTextareaEvent<T extends Event = Event> = T & {
  currentTarget: EventTarget & HTMLTextAreaElement;
};

type TextareaEvents = {
  blur: FormTextareaEvent<FocusEvent>;
  change: FormTextareaEvent<Event>;
  click: FormTextareaEvent<MouseEvent>;
  focus: FormTextareaEvent<FocusEvent>;
  keydown: FormTextareaEvent<KeyboardEvent>;
  keypress: FormTextareaEvent<KeyboardEvent>;
  keyup: FormTextareaEvent<KeyboardEvent>;
  mouseover: FormTextareaEvent<MouseEvent>;
  mouseenter: FormTextareaEvent<MouseEvent>;
  mouseleave: FormTextareaEvent<MouseEvent>;
  paste: FormTextareaEvent<ClipboardEvent>;
  input: FormTextareaEvent<InputEvent>;
};

export {
  Root,
  //
  Root as Textarea,
  type FormTextareaEvent,
  type TextareaEvents,
};
