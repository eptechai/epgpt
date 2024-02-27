<script lang="ts">
  import { ImgType, getImgPath } from '$lib/util/images';
  import classNames from 'classnames';
  import { Spinner } from 'flowbite-svelte';
  import { onMount } from 'svelte';

  export let sampleQuestions: string[];
  export let selectedSampleQuestion: string | undefined;
  export let onSuggestionClick: (question: string) => void;

  let showItems = false;
  onMount(() => {
    setTimeout(() => {
      showItems = true;
    }, 100);
  });
</script>

<div class="container">
  <div class="title">
    <img class="logo" src={getImgPath(ImgType.WideDark)} alt="logo" />
  </div>
  <div class="suggestion-view-container">
    {#each sampleQuestions as question}
      <!-- svelte-ignore a11y-click-events-have-key-events -->
      <!-- svelte-ignore a11y-no-static-element-interactions -->
      <div
        class={classNames('grid-item', showItems ? 'slide-in' : '')}
        on:click={() => {
          onSuggestionClick(question);
        }}
      >
        {question}
        {#if selectedSampleQuestion === question}
          <div class="loading-view">
            <div class="loading-indicator">
              <Spinner size={'8'} />
            </div>
          </div>
        {/if}
      </div>
    {/each}
  </div>
</div>

<style lang="scss">
  @import '../../../global.scss';

  .container {
    display: flex;
    flex-direction: column;
    justify-content: center;
    height: 100%;
  }

  .title {
    opacity: 0.4;
    display: flex;
    justify-content: center;
    align-items: center;
    font-size: 2rem;
    font-weight: 600;
    color: $theme-stale-grey;
    margin-top: 4rem;
  }

  .logo {
    width: 20%;
    min-width: 120px;
    max-width: 200px;
  }

  .suggestion-view-container {
    display: flex;
    flex-wrap: wrap;
    gap: 16px;
    padding: 0px 16px 16px;
    margin: auto auto 0;
    overflow: hidden;
    min-width: 75%;
  }

  .grid-item {
    flex: 1;
    min-width: calc(50% - 8px);
    padding: 16px;
    border: 2px solid #ccc;
    box-sizing: border-box;
    border-radius: 20px;
    cursor: pointer;
    font-weight: 600;
    display: flex;
    align-items: center;
    background-color: transparent; /* Set initial background to transparent */
    opacity: 0;
    transform: translateY(100%); /* Start below the container */
    transition: opacity 0.3s ease-in-out, transform 0.3s ease-in-out;

    &:hover:not(:disabled) {
      background-color: darken(white, 5%);
      cursor: pointer;
    }

    /* Apply the slide-in effect */
    &.slide-in {
      opacity: 1;
      transform: translateY(0); /* Slide up to its original position */
    }
  }

  .loading-view {
    position: absolute;
    top: 0;
    right: 0;
    bottom: 0;
    left: 0;
    z-index: 2;
    background-color: #ffffff9a;

    display: flex;
    justify-content: center;
    align-items: center;
    border-radius: 20px;
    border-radius: 20px;
  }
</style>
