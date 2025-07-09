
import { tool } from "ai";
import { listAssignmentsForUserDataSchema } from "./aitm.schema.ts";
import { listAssignmentsForUser, ListAssignmentsForUserData } from "..";

export default tool({
  description: `
  List assignments for user
Returns the paginated list of assignments for the specified user if the
current user has rights to view. See {api:AssignmentsApiController#index List assignments} for valid
arguments.
    `,
  parameters: listAssignmentsForUserDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListAssignmentsForUserData, "url"> ) => {
    try {
      const { data } = await listAssignmentsForUser(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    