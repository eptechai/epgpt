export enum ImgType {
  InsigniaDark = 'InsigniaDark',
  InsigniaWhite = 'InsigniaWhite',
  TallDark = 'TallDark',
  TallWhite = 'TallWhite',
  WideDark = 'WideDark',
  WideWhite = 'WideWhite',
  WordDark = 'WordDark',
  WordWhite = 'WordWhite',
  BgImgDark = 'BgImgDark',
  BgImgWhite = 'BgImgWhite',
  IconSend = 'IconSend',
  IconAttachment = 'IconAttachment',
  IconScrollToBottom = 'IconScrollToBottom',
  IconClose = 'IconClose',
  IconChat = 'IconChat',
  IconSettings = 'IconSettings',
  IconConfigurations = 'IconConfigurations',
  IconChevronRight = 'IconChevronRight',
  IconChevronLeft = 'IconChevronLeft',
  IconChevronUp = 'IconChevronUp',
  IconChevronDown = 'IconChevronDown',
  IconAdd = 'IconAdd',
  IconAddWhite = 'IconAddWhite',
  IconStop = 'IconStop',
  IconModalClose = 'IconModalClose',
  IconSuccess = 'IconSuccess',
  IconFailure = 'IconFailure',
  IconPending = 'IconPending',
  IconCitation = 'IconCitation',
  IconDelete = 'IconDelete',
  IconDeleteDark = 'IconDeleteDark',
  IconCopy = 'IconCopy',
  IconCheck = 'IconCheck'
}

export const getImgPath = (type: ImgType) => {
  const basePath = '/images/';
  switch (type) {
    case ImgType.InsigniaDark:
      return basePath + 'logos/Teragonia_Insignia_Dark.svg';
    case ImgType.InsigniaWhite:
      return basePath + 'logos/Teragonia_Insignia_White.svg';
    case ImgType.TallDark:
      return basePath + 'logos/Teragonia_Tall_Dark.svg';
    case ImgType.TallWhite:
      return basePath + 'logos/Teragonia_Tall_White.svg';
    case ImgType.WideDark:
      return basePath + 'logos/Teragonia_Wide_Dark.svg';
    case ImgType.WideWhite:
      return basePath + 'logos/Teragonia_Wide_White.svg';
    case ImgType.WordDark:
      return basePath + 'logos/Teragonia_Word_Dark.svg';
    case ImgType.WordWhite:
      return basePath + 'logos/Teragonia_Word_White.svg';
    case ImgType.BgImgDark:
      return basePath + 'images/Teragonia_Bg_Image_Dark.jpg';
    case ImgType.BgImgWhite:
      return basePath + 'images/Teragonia_Bg_Image_White.jpg';
    case ImgType.IconSend:
      return basePath + 'icons/icon_send.png';
    case ImgType.IconAttachment:
      return basePath + 'icons/icon_attachment.png';
    case ImgType.IconScrollToBottom:
      return basePath + 'icons/icon_scroll_to_bottom.png';
    case ImgType.IconClose:
      return basePath + 'icons/icon_close.png';
    case ImgType.IconChat:
      return basePath + 'icons/icon_chat.png';
    case ImgType.IconSettings:
      return basePath + 'icons/icon_settings.png';
    case ImgType.IconConfigurations:
      return basePath + 'icons/icon_configurations.png';
    case ImgType.IconChevronRight:
      return basePath + 'icons/icon_chevron_right.png';
    case ImgType.IconChevronLeft:
      return basePath + 'icons/icon_chevron_left.png';
    case ImgType.IconChevronUp:
      return basePath + 'icons/icon_chevron_up.png';
    case ImgType.IconChevronDown:
      return basePath + 'icons/icon_chevron_down.png';
    case ImgType.IconAdd:
      return basePath + 'icons/icon_add.png';
    case ImgType.IconStop:
      return basePath + 'icons/icon_stop.png';
    case ImgType.IconAddWhite:
      return basePath + 'icons/icon_add_white.png';
    case ImgType.IconModalClose:
      return basePath + 'icons/icon_modal_close.png';
    case ImgType.IconSuccess:
      return basePath + 'icons/icon_success.png';
    case ImgType.IconFailure:
      return basePath + 'icons/icon_failure.png';
    case ImgType.IconPending:
      return basePath + 'icons/icon_pending.png';
    case ImgType.IconCitation:
      return basePath + 'icons/icon_citation.png';
    case ImgType.IconDelete:
      return basePath + 'icons/icon_delete.png';
    case ImgType.IconDeleteDark:
      return basePath + 'icons/icon_delete_dark.png';
    case ImgType.IconCopy:
      return basePath + 'icons/icon_copy.png';
    case ImgType.IconCheck:
      return basePath + 'icons/icon_check.png';
    default:
      throw new Error('Unexpected ImgType - getImgPath');
  }
};
