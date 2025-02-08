/* CONFIDENTIAL AND PROPRIETARY
 * 
 * Copyright (c) 2025 AudioKit.ai. All rights reserved.
 * 
 * This software is confidential and proprietary.
 */

* 
 * This software is confidential and proprietary.
 */

import { Popover as PopoverPrimitive } from 'bits-ui';
import Content from './popover-content.svelte';
const Root = PopoverPrimitive.Root;
const Trigger = PopoverPrimitive.Trigger;
const Close = PopoverPrimitive.Close;

export {
  Close,
  Content,
  //
  Root as Popover,
  Close as PopoverClose,
  Content as PopoverContent,
  Trigger as PopoverTrigger,
  Root,
  Trigger,
};
