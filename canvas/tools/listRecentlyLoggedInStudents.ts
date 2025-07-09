
import { tool } from "ai";
import { listRecentlyLoggedInStudentsDataSchema } from "./aitm.schema.ts";
import { listRecentlyLoggedInStudents, ListRecentlyLoggedInStudentsData } from "..";

export default tool({
  description: `
  List recently logged in students
Returns the paginated list of users in this course, ordered by how
recently they have
logged in. The records include the 'last_login' field which contains
a timestamp
of the last time that user logged into canvas.  The querying
user must have the 'View usage reports'
permission.
    `,
  parameters: listRecentlyLoggedInStudentsDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListRecentlyLoggedInStudentsData, "url"> ) => {
    try {
      const { data } = await listRecentlyLoggedInStudents(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    