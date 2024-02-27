<script lang="ts">
  import { fly } from 'svelte/transition';
  import { onMount, onDestroy } from 'svelte';

  export let subQuestions: string[];
  let activeIndex = 0;
  let interval: ReturnType<typeof setInterval>;

  onMount(() => {
    interval = setInterval(() => {
      if (activeIndex === subQuestions.length - 1) activeIndex = -1;
      activeIndex++;
    }, 2000);
  });

  onDestroy(() => {
    clearInterval(interval);
  });
</script>

<div class="loading-text-wrapper">
  <span>Working on: </span>
  {#each subQuestions as subQuestion, i}
    {#if activeIndex === i}
      <span in:fly={{ y: 1000, duration: 500 }} out:fly={{ y: -1000, duration: 0 }}
        >{subQuestion}</span
      >
    {/if}
  {/each}
</div>

<style>
  .loading-text-wrapper {
    size: 5px;
  }
</style>
