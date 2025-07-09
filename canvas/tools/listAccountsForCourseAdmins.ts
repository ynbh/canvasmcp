
import { tool } from "ai";
import { listAccountsForCourseAdminsDataSchema } from "./aitm.schema.ts";
import { listAccountsForCourseAdmins, ListAccountsForCourseAdminsData } from "..";

export default tool({
  description: `
  List accounts for course admins
A paginated list of accounts that the current user can view through
their
admin course enrollments. (Teacher, TA, or designer enrollments).
Only returns "id", "name",
"workflow_state", "root_account_id" and "parent_account_id"
    `,
  parameters: listAccountsForCourseAdminsDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListAccountsForCourseAdminsData, "url"> ) => {
    try {
      const { data } = await listAccountsForCourseAdmins(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    