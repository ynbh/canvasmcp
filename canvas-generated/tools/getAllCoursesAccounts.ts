
import { tool } from "ai";
import { getAllCoursesAccountsDataSchema } from "./aitm.schema.ts";
import { getAllCoursesAccounts, GetAllCoursesAccountsData } from "..";

export default tool({
  description: `
  Retrieve a paginated list of courses in this account.
    `,
  parameters: getAllCoursesAccountsDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetAllCoursesAccountsData, "url"> ) => {
    try {
      const { data } = await getAllCoursesAccounts(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    