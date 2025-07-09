
import { tool } from "ai";
import { fetchingLatestQuizStatisticsDataSchema } from "./aitm.schema.ts";
import { fetchingLatestQuizStatistics, FetchingLatestQuizStatisticsData } from "..";

export default tool({
  description: `
  Fetching the latest quiz statistics
This endpoint provides statistics for all quiz versions, or for
a specific
quiz version, in which case the output is guaranteed to represent the
_latest_ and most
current version of the quiz.

<b>200 OK</b> response code is returned if the request was successful.
    `,
  parameters: fetchingLatestQuizStatisticsDataSchema.omit({ url: true }),
  execute: async (args : Omit<FetchingLatestQuizStatisticsData, "url"> ) => {
    try {
      const { data } = await fetchingLatestQuizStatistics(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    