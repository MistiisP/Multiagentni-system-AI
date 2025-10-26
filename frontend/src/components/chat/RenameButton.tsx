import React, {useState} from 'react';
import {useChat} from '../../services/chatContext';

interface ChatProps {
    chatID: number;
}

const RenameButton: React.FC<ChatProps> = ({chatID}) => {
    const {renameName} = useChat();
    const [isRename, doneRename] = useState(false);

    const handleSubmit = async (e: React.MouseEvent) => {
        e.stopPropagation();
        const newName = window.prompt("Zadejte nový název");
        if (newName && newName.trim() !== "") {
            doneRename(true);
            await renameName(newName.trim(), chatID);
            doneRename(false);
        }
    };


    return (
        <div className="rename-button">
            <button onClick={handleSubmit} disabled={isRename}><i className='bx  bxs-pencil'  ></i> </button>
        </div>
    )
}

export default RenameButton;