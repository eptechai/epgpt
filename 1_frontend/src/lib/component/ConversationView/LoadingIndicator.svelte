<script lang="ts">
  import classNames from 'classnames';
  import { onMount, onDestroy } from 'svelte';

  let colors = ['#5c57f2', '#5c57f2', '#5c57f2'];
  let colorIndex = 0;

  let interval: ReturnType<typeof setInterval> | undefined;
  let opacities = [
    [1, 0.3, 0.7],
    [0.7, 1, 0.3],
    [0.3, 0.7, 1]
  ];
  let opacityIndex = 0;

  onMount(() => {
    interval = setInterval(() => {
      colorIndex = (colorIndex + 1) % colors.length;
      opacityIndex = (opacityIndex + 1) % opacities.length;
    }, 500);
  });

  onDestroy(() => {
    clearInterval(interval);
  });
</script>

<div class="loading-indicator">
  <div class="circle-container">
    {#each colors as color, index}
      <div
        class={classNames('circle', colorIndex === index ? 'circle-active' : '')}
        style="background-color: {color}; opacity: {opacities[opacityIndex][index]};"
      />
    {/each}
  </div>
</div>

<style>
  .loading-indicator {
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .circle-container {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
  }

  .circle {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    opacity: 0.5;
    margin: 0;
    transition: background-color 0.5s, transform 0.5s;
  }

  .circle-active {
    transform: translateY(-2px);
  }

  .circle-animation {
    animation: fadeAnimation 1s infinite alternate;
  }

  @keyframes fadeAnimation {
    0%,
    100% {
      opacity: 0.5;
    }
    50% {
      opacity: 1;
    }
  }
</style>
