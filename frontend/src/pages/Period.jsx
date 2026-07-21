import { useEffect, useState } from "react";
import api from "../api/api";
import "./periods.css";


function Period() {


    const [startDate,setStartDate] = useState("");

    const [cycleLength,setCycleLength] = useState(28);

    const [periodLength,setPeriodLength] = useState(5);


    const [calendar,setCalendar] = useState(null);

    const [history,setHistory] = useState([]);


    const [message,setMessage] = useState("");

    const [loading,setLoading] = useState(false);




    useEffect(()=>{

        loadCalendar();

        loadHistory();

    },[]);






    async function loadCalendar(){

        try{

            const res = await api.get(
                "/period/calendar"
            );

            setCalendar(res.data);

        }
        catch(error){

            console.log(error);

        }

    }





    async function loadHistory(){

        try{

            const res = await api.get(
                "/period/history"
            );

            setHistory(res.data);

        }
        catch(error){

            console.log(error);

        }

    }






    async function savePeriod(){


        if(!startDate){

            setMessage(
                "Select period start date"
            );

            return;

        }



        setLoading(true);



        try{


            await api.post(

                "/period/",

                {

                    start_date:startDate,

                    period_length:Number(periodLength),

                    cycle_length:Number(cycleLength)

                }

            );



            setMessage(
                "Period saved 🌸"
            );


            loadCalendar();

            loadHistory();


        }

        catch(error){


            console.log(
                error.response?.data
            );


            setMessage(
                error.response?.data?.detail ||
                "Could not save period"
            );


        }


        finally{

            setLoading(false);

        }


    }







    return (

        <div className="period-page">


            <h1>
                🌸 Period Tracker
            </h1>



            <div className="period-layout">



                {/* CALENDAR */}


                <div className="period-card">


                    <h2>
                        📅 Calendar
                    </h2>


                    <input

                        type="date"

                        value={startDate}

                        onChange={
                            e=>setStartDate(e.target.value)
                        }

                    />



                    <input

                        type="number"

                        value={periodLength}

                        onChange={
                            e=>setPeriodLength(e.target.value)
                        }

                        placeholder="Period length"

                    />



                    <input

                        type="number"

                        value={cycleLength}

                        onChange={
                            e=>setCycleLength(e.target.value)
                        }

                        placeholder="Cycle length"

                    />




                    <button
                        onClick={savePeriod}
                    >

                    {
                        loading
                        ?
                        "Saving..."
                        :
                        "Save Period 🌸"
                    }


                    </button>



                    <p>
                        {message}
                    </p>



                </div>







                {/* PREDICTION */}


                <div className="period-card">


                    <h2>
                        🔮 Prediction
                    </h2>



                    {
                        calendar?.next_period &&

                        <>

                        <p>
                        🩸 Next Period:
                        {" "}
                        {calendar.next_period}
                        </p>


                        <p>
                        🥚 Ovulation:
                        {" "}
                        {calendar.ovulation}
                        </p>



                        <p>
                        💗 Fertile Window:
                        {" "}
                        {calendar.fertile_window.start}
                        {" - "}
                        {calendar.fertile_window.end}
                        </p>


                        </>

                    }


                </div>



            </div>







            {/* HISTORY */}


            <div className="period-card history">


                <h2>
                    📖 Period History
                </h2>



                {
                    history.map(item=>(


                        <div
                        key={item.id}
                        className="history-item"
                        >

                        🩸

                        {item.start_date}

                        {" - "}

                        {item.end_date}


                        </div>


                    ))
                }



            </div>



        </div>

    );

}


export default Period;