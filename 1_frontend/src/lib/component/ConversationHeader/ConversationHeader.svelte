<script lang="ts">
  import { ImgType, getImgPath } from '$lib/util/images';
  import classNames from 'classnames';

  export let title = 'Undefined';
  export let scrolled = false;
</script>

<div class={classNames('header', scrolled ? 'header--scrolled' : '')}>
  <div class="logo">
    <img src={getImgPath(ImgType.InsigniaWhite)} alt="Logo" />
  </div>
  <div class="title">{title}</div>
</div>

<style lang="scss">
  .logo {
    position: absolute;
    left: 8px;
    width: 30px;
  }

  .header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    width: 100%;
    color: white;
    padding: 12px 16px;

    position: fixed;
    top: 0;
    left: 0;
    background-color: rgba(51, 51, 51, 0.9);
    color: white;
    transition: background-color 0.3s ease;

    &--scrolled {
      background-color: rgba(51, 51, 51, 0.7);
    }

    .title {
      flex-grow: 1;
      text-align: center;
    }
  }
</style>
