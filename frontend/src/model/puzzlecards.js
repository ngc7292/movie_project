import request from '../util/request.js';  // request 是 demo 项目脚手架中提供的一个做 http 请求的方法，是对于 fetch 的封装，返回 Promise

const delay = (millisecond) => {
  return new Promise((resolve) => {
    setTimeout(resolve, millisecond);
  });
};

export default {
  namespace: 'puzzlecards',
  state: {
    data: [],
    counter: 0,
      },
  effects: {
    *queryInitCards(_, sagaEffects) {
      const { call, put } = sagaEffects;
      // const endPointURI = '/dev/random_joke';

      // const puzzle = yield call(request, endPointURI);
      yield put({ type: 'addNewCard', payload: {setup: '我可以做些什么？', punchline: '你可以试试问我：张子枫是谁'} });

    },
    *askNewQuestion({ payload:newQuestion }, sagaEffects){
      console.log(newQuestion);
      const {call, put} = sagaEffects;
      const checkUrl = "http://121.196.223.97:5000/"+newQuestion;
      console.log(checkUrl);

      const answer = yield call(request, checkUrl);
      console.log(answer);
      yield put({ type: 'addNewCard', payload:{setup:newQuestion, punchline:answer}});
    }
  },
  reducers: {
    addNewCard(state, { payload: newCard }) {
      const nextCounter = state.counter + 1;
      const newCardWithId = { ...newCard, id: nextCounter };
      const nextData = state.data.concat(newCardWithId);
      return {
        data: nextData,
        counter: nextCounter,
      };
    }
  },
};