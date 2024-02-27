<script lang="ts">
  import { page } from '$app/stores';
  import { afterUpdate, onDestroy, onMount } from 'svelte';

  export let value = '';
  export let onSubmit: (text: string) => void;
  export let textareaRef: HTMLTextAreaElement | undefined;
  export let updateMaxHeightDelta: (newDelta: number) => void;
  export let disableNewMsg = false;

  const onKeyDown = (event: KeyboardEvent) => {
    if (event.key === 'Enter' && !event.shiftKey && !disableNewMsg) {
      event.preventDefault();
      if (value.trim() !== '') {
        onSubmit(value.trim());
        value = '';
        adjustTextareaHeight();
      }
    }
  };

  const adjustTextareaHeight = () => {
    if (textareaRef) {
      textareaRef.style.height = 'auto';
      textareaRef.style.height = textareaRef.scrollHeight + 'px';
      updateMaxHeightDelta(textareaRef.scrollHeight);
    }
  };

  const unsubscribe = page.subscribe((currentRoute) => {
    if (currentRoute.url.pathname != null) {
      if (textareaRef != null) {
        textareaRef.focus();
      }
    }
  });

  onMount(() => {
    if (textareaRef != null) {
      textareaRef.focus();
    }
    adjustTextareaHeight();
  });

  afterUpdate(() => {
    adjustTextareaHeight();
  });

  onDestroy(() => {
    unsubscribe();
  });
</script>

<textarea
  bind:value
  bind:this={textareaRef}
  class="textarea"
  placeholder="Message Teragonia..."
  on:keydown={onKeyDown}
  rows={1}
/>

<style lang="scss">
  @import '../../../global.scss';

  .textarea {
    background-color: white;
    color: black;
    border: none;
    resize: none;
    font-size: 18px !important;
    padding: 1em 1.5em;
    box-sizing: border-box;
    width: 100%;
    border-radius: 20px;
    margin-top: 2px;
    max-height: 230px;

    &:hover,
    &:focus,
    &:active {
      outline: none;
    }

    @include custom-scroll-bar();
  }
</style>
