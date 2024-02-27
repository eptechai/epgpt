<script lang="ts">
  import { onMount } from 'svelte';

  export let showModal = false;
  export let dismissable = true;
  let dialog: HTMLDialogElement;

  $: if (dialog) {
    if (showModal) {
      dialog.showModal();
    } else {
      dialog.close();
    }
  }

  onMount(() => {
    if (dismissable) {
      dialog.addEventListener('click', (event) => {
        if (event.target === dialog) {
          showModal = false;
        }
      });
    }
  });
</script>

<dialog bind:this={dialog}>
  <!-- svelte-ignore a11y-click-events-have-key-events -->
  <!-- svelte-ignore a11y-no-static-element-interactions -->

  <div on:click|stopPropagation>
    <slot name="header" />
    <slot />
  </div>
</dialog>

<style lang="scss">
  @import '../../global.scss';
  dialog {
    overflow: visible;
    border-radius: 0.2em;
    border: none;
    padding: 0;
    border-radius: 20px;
    box-shadow: 0 6px 12px lightgray;
  }
  dialog::backdrop {
    background: rgba(255, 255, 255, 0.8);
  }
  dialog > div {
    padding: 2em;
  }
  dialog[open] {
    animation: zoom 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
  }
  @keyframes zoom {
    from {
      transform: scale(0.95);
    }
    to {
      transform: scale(1);
    }
  }
  dialog[open]::backdrop {
    animation: fade 0.2s ease-out;
  }
  @keyframes fade {
    from {
      opacity: 0;
    }
    to {
      opacity: 1;
    }
  }
  button {
    display: block;
  }
</style>
