import { get, writable } from 'svelte/store';

export interface SubQuestionState {
  subQuestionList: string[];
}
const initialState: SubQuestionState = {
  subQuestionList: []
};

const createSubQuestionStore = () => {
  const { subscribe, set } = writable<SubQuestionState>(initialState);

  const createSubQuestionList = (subQuestions: string[]) => {
    set({ subQuestionList: subQuestions });
  };

  const clearSubQuestionList = () => {
    set({ subQuestionList: [] });
  };

  return {
    subscribe,
    clearSubQuestionList,
    createSubQuestionList
  };
};

export const subQuestionListStore = createSubQuestionStore();
export type SubQuestionListStore = ReturnType<typeof createSubQuestionStore>;
