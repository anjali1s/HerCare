import { useState, useEffect } from "react";
import api from "../api/api";
import "./Chat.css";


function Chat() {


  const [message, setMessage] = useState("");

  const [messages, setMessages] = useState([
    {
      sender: "ai",
      text: "Hello! I am HerCare  🌸 How can I support your health today?"
    }
  ]);


  const [conversations, setConversations] = useState([]);

  const [conversationId, setConversationId] = useState(null);

  const [loading, setLoading] = useState(false);



  useEffect(()=>{

    loadConversations();

  },[]);





  async function loadConversations(){

    try{

      const res = await api.get(
        "/chat/conversations"
      );

      setConversations(res.data);

    }
    catch(error){

      console.log(error);

    }

  }






  async function loadChat(id){

    try{

      const res = await api.get(
        `/chat/conversation/${id}`
      );


      setConversationId(id);



      setMessages(

        res.data.map(msg=>({

          sender:
          msg.role==="assistant"
          ?
          "ai"
          :
          "user",

          text:msg.content

        }))

      );


    }
    catch(error){

      console.log(error);

    }

  }







  function newChat(){

    setConversationId(null);


    setMessages([

      {

        sender:"ai",

        text:"Hello! I am HerCare 🌷 How can I help you today?"

      }

    ]);

  }







  async function sendMessage(){


    if(!message.trim())
      return;



    const userText = message;



    setMessages(prev=>[

      ...prev,

      {

        sender:"user",

        text:userText

      }

    ]);



    setMessage("");

    setLoading(true);




    try{


      const response = await api.post(

        "/chat/",

        {

          question:userText,

          conversation_id:conversationId

        }

      );



      setConversationId(

        response.data.conversation_id

      );



      setMessages(prev=>[

        ...prev,

        {

          sender:"ai",

          text:response.data.answer

        }

      ]);



      loadConversations();



    }

    catch(error){


      console.log(error);


      setMessages(prev=>[

        ...prev,

        {

          sender:"ai",

          text:"Sorry 🌸 I could not process your request."

        }

      ]);


    }


    finally{

      setLoading(false);

    }

  }






return (

<div className="chat-layout">


{/* Floating decorations */}

<div className="floating flower-one">
🌸
</div>

<div className="floating flower-two">
🌷
</div>

<div className="floating flower-three">
✨
</div>



<div className="sidebar">


<div className="brand-side">

<h2>
🌸 HerCare Plus
</h2>

<p>
Women's Health AI
</p>

</div>



<button
className="new-chat"
onClick={newChat}
>

💗 New Chat

</button>



<h3>
Previous Chats
</h3>



{
conversations.map(chat=>(


<div

key={chat.id}

className="conversation"

onClick={()=>loadChat(chat.id)}

>

🌷 {chat.title}


</div>


))
}



</div>









<div className="chat-page">



<div className="chat-header">


<div className="logo">

🌸

</div>



<div>

<h2>

HerCare 💗

</h2>


<p>

Your caring AI companion for women's wellness 🌷

</p>


</div>


</div>








<div className="chat-box">


{

messages.map((msg,index)=>(


<div

key={index}

className={
msg.sender==="user"
?
"message user"
:
"message ai"
}

>


{msg.text}


</div>


))

}






{

loading &&

<div className="message ai">

🌸 Thinking...

</div>

}




</div>








<div className="chat-input">


<input


value={message}


onChange={
e=>setMessage(e.target.value)
}



onKeyDown={
e=>{

if(e.key==="Enter")

sendMessage();

}

}


placeholder="Ask HerCare Plus anything 💗"



/>





<button

onClick={sendMessage}

>

Send 🌸

</button>



</div>





</div>



</div>

);


}


export default Chat;