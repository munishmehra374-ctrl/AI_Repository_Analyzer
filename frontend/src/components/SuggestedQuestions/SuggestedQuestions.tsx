import "./SuggestedQuestions.css";

interface Props{

    onSelect:(question:string)=>void;

}

const questions=[

    "Explain the project architecture",

    "Where is Celery used?",

    "Explain authentication",

    "How does retrieval work?"

];

function SuggestedQuestions({

    onSelect,

}:Props){

    return(

        <div className="suggestion-grid">

            {

                questions.map((question)=>(

                    <button

                        key={question}

                        onClick={()=>onSelect(question)}

                    >

                        {question}

                    </button>

                ))

            }

        </div>

    );

}

export default SuggestedQuestions;