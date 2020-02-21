import { Component } from 'react';
import { Layout, Menu, Icon } from 'antd';
const { Header, Footer, Sider, Content } = Layout;
import Link from 'umi/link';

// 引入子菜单组件
const SubMenu = Menu.SubMenu;

export default class BasicLayout extends Component {
  render() {
    return (
      <Layout>
        <Sider width={256} style={{ minHeight: '100vh' }}>
          <div style={{ height: '32px', background: 'rgba(255,255,255,.2)', margin: '16px'}}/>
          <Menu theme="dark" mode="inline" defaultSelectedKeys={['1']}>
            <Menu.Item key="1">
              <Link to="/puzzlecards">
                <Icon type="pie-chart" />
                <span>puzzlecards</span>
              </Link>
            </Menu.Item>
            <Menu.Item key="2">
              <Link to="/earth">
                <Icon type="pie-chart" />
                <span>Earth</span>
              </Link>
            </Menu.Item>
            
          </Menu>
        </Sider>
        
        <Layout >
          <Header style={{ background: '#fff', textAlign: 'center', padding: 0 }}>Header</Header>
          <Content style={{ margin: '24px 16px 0' , width:'100%'}}>
            <div style={{ padding: 24, background: '#fff', minHeight: 360 ,width:'100%'}}>
              {this.props.children}
            </div>
          </Content>
          <Footer style={{ textAlign: 'center' }}>Ant Design ©2018 Created by Ant UED</Footer>
        </Layout>
      </Layout>
    )
  }
}