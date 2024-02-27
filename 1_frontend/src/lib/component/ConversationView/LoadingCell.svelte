<script lang="ts">
  import { ImgType, getImgPath } from '$lib/util/images';
  import SubQuestionLoadingIndicator from './SubQuestionLoadingIndicator.svelte';
  import LoadingIndicator from './LoadingIndicator.svelte';
  import { useContexts, ContextType } from '$lib/context';
  import { onDestroy } from 'svelte';
  import type { SubQuestionState } from '../../../stores/subQuestionListStore';

  const { subQuestionListStore } = useContexts([ContextType.SUBQUESTION_LIST_STORE]);

  let subQuestionListState: SubQuestionState;
  const unsubscribe = subQuestionListStore.subscribe((value) => {
    subQuestionListState = value;
  });

  let subQuestions: string[] = [];
  $: subQuestions = subQuestionListState.subQuestionList;

  onDestroy(() => {
    unsubscribe();
  });
</script>

<div class="message-item">
  <div class="message-wrapper">
    <div class="icon-wrapper">
      <div class="icon">
        <img class="logo" src={getImgPath(ImgType.InsigniaDark)} alt="TRG" />
      </div>
    </div>
    <div class="message-container">
      <div class="message">
        <LoadingIndicator />
      </div>
      {#if subQuestions && subQuestions.length > 0}
        <SubQuestionLoadingIndicator {subQuestions} />
      {/if}
    </div>
  </div>
</div>

<style lang="scss">
  @import '../../../global.scss';

  :global(.card-header) {
    cursor: pointer;
    user-select: none;
    width: 100%;
  }

  .message-item {
    display: flex;
    align-items: center;
    justify-content: flex-start;
    margin: 8px;
    padding: 8px;
    border-radius: 16px;
  }

  .message-wrapper {
    display: flex;
    align-items: center;
    gap: 8px;
    width: 100%;
  }

  .message-container {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
  }

  .message {
    flex: 1;
    padding: 12px 16px;
    border-radius: 16px;
    background-color: white;
    flex-wrap: wrap;
    word-wrap: break-word;
    box-shadow: 0 4px 6px $theme-stale-light-grey;
    overflow-wrap: break-word;
    margin-bottom: 8px;
  }

  .icon-wrapper {
    width: 40px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    align-self: flex-start; // TODO: move every icon to flex-start
  }

  .icon {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 40px;
    height: 40px;
    border-radius: 50%;
    border: 2px solid $theme-stale-light-grey;
    font-weight: bold;
  }

  .logo {
    padding: 7px;
  }
</style>
