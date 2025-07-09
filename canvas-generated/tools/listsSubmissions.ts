
import { tool } from "ai";
import { listsSubmissionsDataSchema } from "./aitm.schema.ts";
import { listsSubmissions, ListsSubmissionsData } from "..";

export default tool({
  description: `
  Lists submissions
Gives a nested list of submission versions
    `,
  parameters: listsSubmissionsDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListsSubmissionsData, "url"> ) => {
    try {
      const { data } = await listsSubmissions(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    