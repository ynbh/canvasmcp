
import { tool } from "ai";
import { getAvailableQuizIpFiltersDataSchema } from "./aitm.schema.ts";
import { getAvailableQuizIpFilters, GetAvailableQuizIpFiltersData } from "..";

export default tool({
  description: `
  Get available quiz IP filters.
Get a list of available IP filters for this Quiz.

<b>200 OK</b>
response code is returned if the request was successful.
    `,
  parameters: getAvailableQuizIpFiltersDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetAvailableQuizIpFiltersData, "url"> ) => {
    try {
      const { data } = await getAvailableQuizIpFilters(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    