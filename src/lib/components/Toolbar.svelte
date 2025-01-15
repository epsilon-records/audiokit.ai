<script lang="ts">
  import { Editor } from '@tiptap/core';
  import { Bold, Italic, List, ListOrdered, Link, Quote } from 'svelte-hero-icons';

  export let editor: Editor | null = null;
  export let disabled = false;

  const buttons = [
    {
      icon: Bold,
      title: 'Bold',
      action: () => editor?.chain().focus().toggleBold().run(),
      isActive: () => editor?.isActive('bold'),
    },
    {
      icon: Italic,
      title: 'Italic',
      action: () => editor?.chain().focus().toggleItalic().run(),
      isActive: () => editor?.isActive('italic'),
    },
    {
      icon: List,
      title: 'Bullet List',
      action: () => editor?.chain().focus().toggleBulletList().run(),
      isActive: () => editor?.isActive('bulletList'),
    },
    {
      icon: ListOrdered,
      title: 'Ordered List',
      action: () => editor?.chain().focus().toggleOrderedList().run(),
      isActive: () => editor?.isActive('orderedList'),
    },
    {
      icon: Quote,
      title: 'Blockquote',
      action: () => editor?.chain().focus().toggleBlockquote().run(),
      isActive: () => editor?.isActive('blockquote'),
    },
    {
      icon: Link,
      title: 'Link',
      action: () => {
        const url = window.prompt('Enter URL');
        if (url) {
          editor?.chain().focus().setLink({ href: url }).run();
        }
      },
      isActive: () => editor?.isActive('link'),
    },
  ];
</script>

<div class="border-b p-2 flex flex-wrap gap-2">
  {#each buttons as button}
    <button
      type="button"
      class="p-2 rounded-lg hover:bg-muted transition-colors {button.isActive() ? 'bg-muted' : ''}"
      on:click={button.action}
      disabled={!editor || disabled}
      title={button.title}
    >
      <svelte:component this={button.icon} class="w-5 h-5" aria-hidden="true" />
    </button>
  {/each}
</div>
