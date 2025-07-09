
import { tool } from "ai";
import { listMissingSubmissionsDataSchema } from "./aitm.schema.ts";
import { listMissingSubmissions, ListMissingSubmissionsData } from "..";

export default tool({
  description: `
  List Missing Submissions
A paginated list of past-due assignments for which the student does not
have a submission.
The user sending the request must either be the student, an admin or a parent
observer using the parent app
    `,
  parameters: listMissingSubmissionsDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListMissingSubmissionsData, "url"> ) => {
    try {
      const { data } = await listMissingSubmissions(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    