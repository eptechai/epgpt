<script lang="ts">
  import { ImgType, getImgPath } from '$lib/util/images';
  import classNames from 'classnames';
  import ReferencesView from './ReferencesView.svelte';
  import { Tooltip } from 'flowbite-svelte';
  import type { ResponseItem } from '$lib/types';
  import CollapsibleCard from '../CollapsibleCard/CollapsibleCard.svelte';
  import {
    ThumbsUpOutline,
    ThumbsUpSolid,
    CheckSolid,
    ClipboardOutline,
    ThumbsDownSolid,
    ThumbsDownOutline
  } from 'flowbite-svelte-icons';

  export let item: ResponseItem;
  export let rateResponse: (messageId: string, isFeedbackPositive: boolean | null) => void;
  export let conversationId: string;

  $: hasReferences = item.response.citations.length > 0;
  let copied = false;

  let positiveFeedback: boolean | null;
  $: positiveFeedback = item.response.isFeedbackPositive;

  function handleLike() {
    if (positiveFeedback) positiveFeedback = null;
    else positiveFeedback = true;
    item.response.isFeedbackPositive = positiveFeedback;
    handleFeedbackChange(positiveFeedback);
  }

  function handleDislike() {
    if (positiveFeedback === false) positiveFeedback = null;
    else positiveFeedback = false;
    item.response.isFeedbackPositive = positiveFeedback;
    handleFeedbackChange(positiveFeedback);
  }

  const handleFeedbackChange = (isFeedbackPositive: boolean | null) => {
    rateResponse(item.response.id, isFeedbackPositive);
  };

  function handleCopy() {
    navigator.clipboard.writeText(item.response.response);
    copied = true;

    setTimeout(() => {
      copied = false;
    }, 2000);
  }
</script>

<div>
  <CollapsibleCard>
    <div
      id="message-cell-trigger-{item.response.id}"
      slot="header"
      class={classNames('message-item', hasReferences ? 'citations' : '')}
    >
      <div class="message-wrapper">
        <div class="icon-wrapper">
          <div class="icon">
            <img class="logo" src={getImgPath(ImgType.InsigniaDark)} alt="TRG" />
          </div>
        </div>
        <div class="message">{item.response.response}</div>
        {#if hasReferences}
          <img
            class="citation-icon"
            src={getImgPath(ImgType.IconCitation)}
            alt="citation"
            width={40}
          />
        {/if}
      </div>
    </div>

    <div class="action-view" slot="buttons">
      <button class="action-button" on:click={handleCopy}>
        {#if !copied}
          <ClipboardOutline
            class="outline-none hover:text-theme-blue text-theme-stale-grey"
            size="sm"
            role="img"
            strokeWidth="1.2"
          />
        {:else}
          <CheckSolid class="outline-none text-theme-blue" size="sm" role="img" strokeWidth="1.2" />
        {/if}
      </button>
      <button class="action-button" on:click={handleLike}>
        {#if positiveFeedback}
          <ThumbsUpSolid
            class="outline-none text-theme-blue"
            size="sm"
            role="img"
            strokeWidth="1.2"
          />
        {:else}
          <ThumbsUpOutline
            class="outline-none hover:text-theme-blue text-theme-stale-grey"
            size="sm"
            role="img"
            strokeWidth="1.2"
          />
        {/if}
      </button>
      <button class="action-button" on:click={handleDislike}>
        {#if positiveFeedback === false}
          <ThumbsDownSolid
            class="outline-none text-theme-blue"
            size="sm"
            role="img"
            strokeWidth="1.2"
          />
        {:else}
          <ThumbsDownOutline
            class="outline-none text-theme-stale-grey hover:text-theme-blue"
            size="sm"
            role="img"
            strokeWidth="1.2"
          />
        {/if}
      </button>
    </div>
    <div slot="body">
      <ReferencesView citations={item.response.citations} {conversationId} />
    </div>
  </CollapsibleCard>

  {#if hasReferences}
    <Tooltip
      placement={'top-start'}
      triggeredBy="#message-cell-trigger-{item.response.id}"
      type="custom"
      defaultClass=""
      class="p-2 text-md font-medium bg-theme-orange text-white"
      arrow={false}
    >
      Click and View Citations
    </Tooltip>
  {/if}
</div>

<style lang="scss">
  @import '../../../global.scss';

  $button-size: 25px;

  :global(.card-header) {
    cursor: pointer;
    user-select: text;
    width: 100%;
  }

  .message-item {
    display: flex;
    align-items: center;
    justify-content: flex-start;
    margin: 8px;
    padding: 8px;
    border-radius: 16px;
    cursor: default;
    user-select: text;

    &.citations {
      cursor: pointer;

      &:hover:not(:disabled) {
        background-color: darken(white, 5%);

        .citation-icon:not(:disabled) {
          transform: scale(1.1);
        }
      }
    }
  }

  .message-wrapper {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-right: 48px;
  }

  .message {
    flex: 1;
    padding: 12px 16px;
    border-radius: 16px;
    background-color: white;
    box-shadow: 0 4px 6px $theme-stale-light-grey;
    overflow-wrap: break-word;
    text-align: start;
    white-space: pre-line;
    min-height: 45px;
  }

  .icon-wrapper {
    width: 40px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    align-self: flex-start;
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

  .citation-icon {
    padding: 7px;
  }

  .action-view {
    display: flex;
    height: 30px;
    margin-left: 2px;
    gap: 4px;
  }

  .copied-view {
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: center;
    gap: 4px;
    height: 30px;
  }

  .copied-icon {
    width: 24px;
    height: 24px;
  }

  .copied-text {
    font-size: 14px;
    font-weight: bold;
    color: $theme-blue;
    margin-top: 2px;
  }

  .action-button {
    height: $button-size;
    width: $button-size;
    cursor: pointer;
    border-radius: 50%;
    background-color: transparent;
    padding: 5px;
    margin-right: -7px;
    margin-top: -7px;
    width: 30px;
    height: 30px;

    &:active {
      transform: translateY(1px);
      box-shadow: none;
    }
  }
</style>
