import type { InputType } from 'flowbite-svelte';
import type { ParamsResponse } from '../../../generated/client';

export type NumericParamsResponseKey = Exclude<keyof ParamsResponse, 'use_only_uploaded'>;
export type ParamsResponseItem = {
  value: NumericParamsResponseKey;
  name: string;
};
export type NumericParamsResponseKeyArray = NumericParamsResponseKey[];

export function getDefaultParams(): ParamsResponse {
  const defaultParams: ParamsResponse = {
    qe_k: 5,
    qe_top_k: 5,
    qe_temperature: 0.25,
    qe_max_new_tokens: 250,
    qe_score_threshold: 0.7,
    qe_repetition_penalty: 1.2,
    rs_k: 5,
    rs_top_k: 5,
    rs_temperature: 0.25,
    rs_max_new_tokens: 250,
    rs_score_threshold: 0.7,
    rs_repetition_penalty: 1.2,
    use_only_uploaded: false
  };

  return defaultParams;
}

// Note: we need string response for reflecting the `.` user has input
export type LocalParamsResponse = {
  qe_k: string;
  qe_top_k: string;
  qe_temperature: string;
  qe_max_new_tokens: string;
  qe_score_threshold: string;
  qe_repetition_penalty: string;
  rs_k: string;
  rs_top_k: string;
  rs_temperature: string;
  rs_max_new_tokens: string;
  rs_score_threshold: string;
  rs_repetition_penalty: string;
  use_only_uploaded: boolean;
};
export const convertParamsResponsetoLocalParamsResponse = (
  paramsResponse: ParamsResponse
): LocalParamsResponse => {
  const {
    qe_k,
    qe_top_k,
    qe_temperature,
    qe_max_new_tokens,
    qe_score_threshold,
    qe_repetition_penalty,
    rs_k,
    rs_top_k,
    rs_temperature,
    rs_max_new_tokens,
    rs_score_threshold,
    rs_repetition_penalty,
    use_only_uploaded
  } = paramsResponse;

  return {
    qe_k: qe_k.toString(),
    qe_top_k: qe_top_k.toString(),
    qe_temperature: qe_temperature.toString(),
    qe_max_new_tokens: qe_max_new_tokens.toString(),
    qe_score_threshold: qe_score_threshold.toString(),
    qe_repetition_penalty: qe_repetition_penalty.toString(),
    rs_k: rs_k.toString(),
    rs_top_k: rs_top_k.toString(),
    rs_temperature: rs_temperature.toString(),
    rs_max_new_tokens: rs_max_new_tokens.toString(),
    rs_score_threshold: rs_score_threshold.toString(),
    rs_repetition_penalty: rs_repetition_penalty.toString(),
    use_only_uploaded
  };
};
const parameterInputStrToNumber = (
  inputStr: string,
  fieldName: NumericParamsResponseKey
): number => {
  if (isNaN(parseFloat(inputStr))) {
    return getDefaultParams()[fieldName];
  }

  return Math.round(parseFloat(inputStr) * 100) / 100;
};
export const convertLocalParamsResponsetoParamsResponse = (
  localParamsResponse: LocalParamsResponse
): ParamsResponse => {
  const {
    qe_k,
    qe_top_k,
    qe_temperature,
    qe_max_new_tokens,
    qe_score_threshold,
    qe_repetition_penalty,
    rs_k,
    rs_top_k,
    rs_temperature,
    rs_max_new_tokens,
    rs_score_threshold,
    rs_repetition_penalty,
    use_only_uploaded
  } = localParamsResponse;

  return {
    qe_k: parameterInputStrToNumber(qe_k, 'qe_k'),
    qe_top_k: parameterInputStrToNumber(qe_top_k, 'qe_top_k'),
    qe_temperature: parameterInputStrToNumber(qe_temperature, 'qe_temperature'),
    qe_max_new_tokens: parameterInputStrToNumber(qe_max_new_tokens, 'qe_max_new_tokens'),
    qe_score_threshold: parameterInputStrToNumber(qe_score_threshold, 'qe_score_threshold'),
    qe_repetition_penalty: parameterInputStrToNumber(
      qe_repetition_penalty,
      'qe_repetition_penalty'
    ),
    rs_k: parameterInputStrToNumber(rs_k, 'rs_k'),
    rs_top_k: parameterInputStrToNumber(rs_top_k, 'rs_top_k'),
    rs_temperature: parameterInputStrToNumber(rs_temperature, 'rs_temperature'),
    rs_max_new_tokens: parameterInputStrToNumber(rs_max_new_tokens, 'rs_max_new_tokens'),
    rs_score_threshold: parameterInputStrToNumber(rs_score_threshold, 'rs_score_threshold'),
    rs_repetition_penalty: parameterInputStrToNumber(
      rs_repetition_penalty,
      'rs_repetition_penalty'
    ),
    use_only_uploaded
  };
};

export type ParamViewConfig = {
  [key in NumericParamsResponseKey]: {
    label: string;
    fieldName: NumericParamsResponseKey;
    placeholder: string;
    type: InputType;
    min: number;
    max: number;
    value?: string;
  };
};
export const allParamViewConfigs: ParamViewConfig = {
  qe_k: {
    label: 'QE K',
    fieldName: 'qe_k',
    placeholder: 'Please enter K',
    type: 'number',
    min: 1,
    max: 15
  },
  rs_k: {
    label: 'RS K',
    fieldName: 'rs_k',
    placeholder: 'Please enter K',
    type: 'number',
    min: 1,
    max: 15
  },
  qe_top_k: {
    label: 'QE Top K',
    fieldName: 'qe_top_k',
    placeholder: 'Please enter Top K',
    type: 'number',
    min: 1,
    max: 25
  },
  rs_top_k: {
    label: 'RS Top K',
    fieldName: 'rs_top_k',
    placeholder: 'Please enter Top K',
    type: 'number',
    min: 1,
    max: 25
  },
  qe_max_new_tokens: {
    label: 'QE Max New Token',
    fieldName: 'qe_max_new_tokens',
    placeholder: 'Please enter Max New Token',
    type: 'number',
    min: 1,
    max: 500
  },
  rs_max_new_tokens: {
    label: 'RS Max New Token',
    fieldName: 'rs_max_new_tokens',
    placeholder: 'Please enter Max New Token',
    type: 'number',
    min: 1,
    max: 500
  },
  qe_temperature: {
    label: 'QE Temperature',
    fieldName: 'qe_temperature',
    placeholder: 'Please enter Temperature',
    type: 'number',
    min: 0,
    max: 3
  },
  rs_temperature: {
    label: 'RS Temperature',
    fieldName: 'rs_temperature',
    placeholder: 'Please enter Temperature',
    type: 'number',
    min: 0,
    max: 3
  },
  qe_score_threshold: {
    label: 'QE Score Threshold',
    fieldName: 'qe_score_threshold',
    placeholder: 'Please enter QE Score Threshold',
    type: 'number',
    min: 0,
    max: 5
  },
  rs_score_threshold: {
    label: 'RS Score Threshold',
    fieldName: 'rs_score_threshold',
    placeholder: 'Please enter RS Score Threshold',
    type: 'number',
    min: 0,
    max: 5
  },
  qe_repetition_penalty: {
    label: 'QE Repetition Penalty',
    fieldName: 'qe_repetition_penalty',
    placeholder: 'Please enter QE Repetition Penalty',
    type: 'number',
    min: 0,
    max: 2.0
  },
  rs_repetition_penalty: {
    label: 'RS Repetition Penalty',
    fieldName: 'rs_repetition_penalty',
    placeholder: 'Please enter RS Repetition Penalty',
    type: 'number',
    min: 0,
    max: 2.0
  }
};

// Note: Default Selected Items
export const defaultSelectedParams: NumericParamsResponseKeyArray = [
  'qe_max_new_tokens',
  'qe_temperature',
  'rs_max_new_tokens',
  'rs_temperature'
];
export const defaultSelectedParamItems: ParamsResponseItem[] = defaultSelectedParams.map((it) => ({
  value: it,
  name: allParamViewConfigs[it].label
}));

// Note: All the options we have
export const allParamOptions: NumericParamsResponseKeyArray = [
  'qe_max_new_tokens',
  'qe_temperature',
  'rs_max_new_tokens',
  'rs_temperature',
  'qe_k',
  'rs_k',
  'qe_top_k',
  'rs_top_k',
  'qe_score_threshold',
  'rs_score_threshold',
  'qe_repetition_penalty',
  'rs_repetition_penalty'
];
export const allParamOptionItems: ParamsResponseItem[] = allParamOptions.map((it) => ({
  value: it,
  name: allParamViewConfigs[it].label
}));
