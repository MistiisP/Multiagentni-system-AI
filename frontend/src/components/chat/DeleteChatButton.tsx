import React, {useState} from 'react';
import {useChat} from '../../services/chatContext';

interface ChatProps{
    chatID: number;
}

const DeleteChatButton: React.FC<ChatProps> = ({chatID}) => {
    const {deleteChat} = useChat();
    const [isDeleting, doneDeleting] = useState(false);

    const handleSubmit = async (e: React.MouseEvent) => {
        e.stopPropagation();
        if (window.confirm("Opravdu chcete smazat konverzaci?")) {
            doneDeleting(true);
            await deleteChat(chatID);
            doneDeleting(false);
        }
    }

    return (
        <div className="delete-button">
            <button onClick={handleSubmit} disabled={isDeleting}><i className='bx bxs-trash'  ></i> </button>
        </div>
    )
}

export default DeleteChatButton;