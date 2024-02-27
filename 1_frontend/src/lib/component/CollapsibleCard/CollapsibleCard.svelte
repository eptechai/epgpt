<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import collapse from './collapsible';

  export let open = false;
  export let duration = 0.2;
  export let easing = 'ease';

  const dispatch = createEventDispatcher();

  function handleToggle() {
    open = !open;

    if (open) {
      dispatch('open');
    } else {
      dispatch('close');
    }
  }
</script>

<div class="card" class:open aria-expanded={open}>
  <button type="button" class="card-header" on:click={handleToggle}>
    <slot name="header" />
  </button>

  <div class="button-wrapper">
    <slot name="buttons" />
  </div>

  <div class="card-body" use:collapse={{ open, duration, easing }}>
    <slot name="body" />
  </div>
</div>

<style lang="scss">
  .card-header {
    cursor: pointer;
    user-select: none;
    background: transparent;
    border: none !important;
  }

  .button-wrapper {
    display: flex;
    justify-content: flex-start;
    margin-top: -8px;
    margin-left: 62px;
  }

  .card-body {
    margin-top: 15px;
    margin-left: 48px;
  }
</style>
