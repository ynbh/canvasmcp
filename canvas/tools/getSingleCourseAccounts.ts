
import { tool } from "ai";
import { getSingleCourseAccountsDataSchema } from "./aitm.schema.ts";
import { getSingleCourseAccounts, GetSingleCourseAccountsData } from "..";

export default tool({
  description: `
  Get a single course
Return information on a single course. Accepts the same include[] parameters as
the list action plus:
    `,
  parameters: getSingleCourseAccountsDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetSingleCourseAccountsData, "url"> ) => {
    try {
      const { data } = await getSingleCourseAccounts(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    