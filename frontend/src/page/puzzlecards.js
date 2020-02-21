import React, { Component } from 'react';
import { Card ,Button,Input } from 'antd';
import { connect } from 'dva';


const namespace = 'puzzlecards';
const { Search } = Input;

const mapStateToProps = (state) => {
  const cardList = state[namespace].data;
  return {
    cardList,
  };
};

const mapDispatchToProps = (dispatch) => {
  return {
    onDidMount: () => {
      dispatch({
        type: `${namespace}/queryInitCards`,
      });
    },
    onSearch: (newquestion) =>{
      dispatch({
        type: `${namespace}/askNewQuestion`,
        payload: newquestion,
      })
    }
  };
};

@connect(mapStateToProps, mapDispatchToProps)
export default class PuzzleCardsPage extends Component {
  componentDidMount() {
    this.props.onDidMount();
  }
  render() {
    return (
      <div>
        {
          this.props.cardList.map(card => {
            return (
              <Card key={card.id}>
                <div>Q: {card.setup}</div>
                <div>
                  <strong>A: {card.punchline}</strong>
                </div>
              </Card>
            );
          })
        }
        <Search 
          placeholder="input search text"
          enterButton="Search"
          size="large"
          onSearch={value => this.props.onSearch(value)} 
          />
      </div>
    );
  }
}