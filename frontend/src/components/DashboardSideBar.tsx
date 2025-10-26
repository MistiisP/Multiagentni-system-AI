import React, { useState } from 'react';
import SideBarButtons from './chat/SideBarButtons';
import ListOfChats from './chat/ListOfChats';
import '../css/Chat.css';

const DashboardSideBar: React.FC = () => {
  const [isSidebarVisible, setIsSidebarVisible] = useState(false);

  const toggleSidebar = () => {
    setIsSidebarVisible(!isSidebarVisible);
  };

  return (
    <>
      <button className="sidebar-toggle-button" onClick={toggleSidebar}
        style={{ top: '50vh', left: isSidebarVisible ? '270px' : '20px', zIndex: 101, transition: 'left 0.3s ease'}} >
        <i className={`bx ${isSidebarVisible ? 'bx-chevron-left' : 'bx-chevron-right'}`}></i>
      </button>
      <div className={`dashboard-sidebar ${isSidebarVisible ? 'active' : ''}`}>
        <div className="sidebar-new-chat">
          <SideBarButtons />
        </div>
        <div className="sidebar-list-chats">
          <ListOfChats />
        </div>
      </div>
    </>
  );
};

export default DashboardSideBar;