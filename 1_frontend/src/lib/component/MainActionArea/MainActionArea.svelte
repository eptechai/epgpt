<script lang="ts">
  import classNames from 'classnames';
  import TextAreaAutosize from './TextAreaAutosize.svelte';
  import { ImgType, getImgPath } from '$lib/util/images';

  export let onSubmit: (text: string) => void;
  export let textareaRef: HTMLTextAreaElement | undefined;
  export let updateMaxHeightDelta: (textareaDelta: number) => void = () => {};
  export let errorMessage: string | undefined = undefined;
  export let disableNewMsg = false;

  let text = '';
  let fileInput: HTMLInputElement;

  const clearFileInput = () => {
    if (fileInput) {
      fileInput.value = '';
    }
  };

  const submitWithKey = (text: string) => {
    onSubmit(text);
    clearFileInput();
  };

  const submitWithBtn = () => {
    onSubmit(text);
    text = '';
    clearFileInput();
  };
</script>

<div class="outer-wrapper">
  <div class={classNames('textarea__wrapper', !!errorMessage && 'textarea__wrapper__error')}>
    <div class="textarea__main">
      <TextAreaAutosize
        bind:value={text}
        {textareaRef}
        onSubmit={submitWithKey}
        {updateMaxHeightDelta}
        {disableNewMsg}
      />
      {#if !!errorMessage}
        <div class="error-container">{errorMessage}</div>
      {/if}
    </div>

    <div class="textarea__actions">
      <button
        class={classNames('textarea__button', 'send-button')}
        on:click={submitWithBtn}
        disabled={text.trim() === '' || disableNewMsg}
      >
        <img src={getImgPath(ImgType.IconSend)} alt="Send" />
      </button>
    </div>
  </div>
</div>

<style lang="scss">
  @import '../../../global.scss';
  $button-bg-color: #2ecc71;
  $button-bg-color-disabled: #cccccc;

  .outer-wrapper {
    display: flex;
    flex-direction: row;
    width: 100%;
    justify-content: center;
    align-items: center;
    gap: 16px;
  }

  .textarea {
    &__wrapper {
      display: flex;
      flex-direction: row;
      align-items: center;
      margin-top: auto;
      resize: none;
      background-color: white;
      border-radius: 40px;
      width: 100%;
      padding: 0px 24px;
      box-shadow: 0 4px 6px $theme-stale-light-grey;

      &__error {
        border: 4px solid red;
      }
    }

    &__button {
      color: white;
      font-size: 14px;
      cursor: pointer;

      border-radius: 50%;
      transition: background-color 0.3s ease-in-out;
      align-self: flex-end;
      width: 40px;
      height: 40px;

      position: relative;
      padding: 8px 10px 8px 8px;
      box-shadow: 0 4px 6px $theme-stale-light-grey;
      align-self: center;

      &__file-input {
        position: absolute;
        opacity: 0;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        cursor: pointer;
        z-index: 1;
      }
    }

    &__main {
      display: flex;
      flex-direction: column;
      width: 100%;
    }

    &__actions {
      display: flex;
      flex-direction: row;
      justify-content: center;
      align-items: center;
      gap: 8px;
      padding: 12px 0;
      align-self: flex-end;
    }

    &__submit-icon {
      font-size: 10px;
    }
  }

  .send-button {
    background-color: $theme-charcoal;

    &:hover:not(:disabled) {
      background-color: darken($theme-charcoal, 10%);
      cursor: pointer;
    }

    &:disabled {
      background-color: #dedede;
      cursor: not-allowed;
    }
  }

  .send-button-outer {
    background-color: $theme-blue;
    box-shadow: none;

    &:hover:not(:disabled) {
      background-color: darken($theme-blue, 10%);
      cursor: pointer;
    }

    &:disabled {
      background-color: $theme-light-grey;
      cursor: not-allowed;
    }
  }

  .error-container {
    color: red;
    font-weight: 600;
    padding: 2px 12px;
  }
</style>
