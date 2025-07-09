
import { tool } from "ai";
import { getCurrentQuizSubmissionTimesDataSchema } from "./aitm.schema.ts";
import { getCurrentQuizSubmissionTimes, GetCurrentQuizSubmissionTimesData } from "..";

export default tool({
  description: `
  Get current quiz submission times.
Get the current timing data for the quiz attempt, both the end_at
timestamp
and the time_left parameter.

<b>Responses</b>

* <b>200 OK</b> if the request was
successful
    `,
  parameters: getCurrentQuizSubmissionTimesDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetCurrentQuizSubmissionTimesData, "url"> ) => {
    try {
      const { data } = await getCurrentQuizSubmissionTimes(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    