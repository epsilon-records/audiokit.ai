<script lang="ts">
  import { Editor as TiptapEditor } from '@tiptap/core';
  import StarterKit from '@tiptap/starter-kit';
  import Link from '@tiptap/extension-link';
  import { onMount, onDestroy } from 'svelte';
  // import Toolbar from '$lib/components/Toolbar.svelte';

  export let value = '';
  export let placeholder = 'Start writing...';
  export let disabled = false;
  export let id: string;

  let element: HTMLElement;
  let editor: TiptapEditor;

  $: if (editor && disabled) {
    editor.setEditable(!disabled);
  }

  onMount(() => {
    editor = new TiptapEditor({
      element,
      extensions: [
        StarterKit,
        Link.configure({
          openOnClick: false,
          HTMLAttributes: {
            class: 'text-primary underline cursor-pointer',
          },
        }),
      ],
      content: value,
      editable: !disabled,
      editorProps: {
        attributes: {
          id,
          class: 'prose dark:prose-invert max-w-none focus:outline-none',
        },
      },
      onUpdate: ({ editor }) => {
        const newContent = editor.getHTML();
        value = newContent;
        // Dispatch change event for form handling
        element.dispatchEvent(new CustomEvent('change', { detail: newContent }));
      },
    });
  });

  onDestroy(() => {
    if (editor) {
      editor.destroy();
    }
  });
</script>

<div class="editor-wrapper rounded-md border">
  <!-- <Toolbar {editor} {disabled} /> -->
  <div class="min-h-[200px] w-full p-4 prose dark:prose-invert max-w-none" bind:this={element} />
</div>

<style>
  :global(.ProseMirror p.is-editor-empty:first-child::before) {
    content: attr(data-placeholder);
    float: left;
    color: #adb5bd;
    pointer-events: none;
    height: 0;
  }

  :global(.ProseMirror) {
    > * + * {
      margin-top: 0.75em;
    }
  }
</style>
