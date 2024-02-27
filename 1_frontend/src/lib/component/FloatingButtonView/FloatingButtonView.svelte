<script lang="ts">
  import { ImgType, getImgPath } from '$lib/util/images';
  import classNames from 'classnames';

  export let onAttachnmentClick: () => void;
  export let onConfigurationClick: () => void;
  export let mobileMode: boolean;
  export let isPendingCreation: boolean;
</script>

<div class={classNames('floating-button-view', mobileMode ? 'mobile-mode' : '')}>
  {#if !isPendingCreation}
    <button class="attachment-button" on:click={onAttachnmentClick}>
      <img width={36} src={getImgPath(ImgType.IconAttachment)} alt="Attachments" />
    </button>
  {/if}
  <button class="configure-button" on:click={onConfigurationClick}>
    <img width={36} src={getImgPath(ImgType.IconConfigurations)} alt="Configurations" />
  </button>
</div>

<style lang="scss">
  @import '../../../global.scss';

  .floating-button-view {
    display: flex;
    flex-direction: column;
    align-items: center;

    position: absolute;
    right: 12px;
    bottom: 12px;

    &.mobile-mode {
      right: 12px;
      top: 90px;
    }
  }

  .attachment-button {
    @include icon-button-styles($theme-blue, 56px);
  }

  .configure-button {
    @include icon-button-styles($theme-skyblue, 56px);
  }
</style>
