
import { tool } from "ai";
import { listPotentialMembersCoursesDataSchema } from "./aitm.schema.ts";
import { listPotentialMembersCourses, ListPotentialMembersCoursesData } from "..";

export default tool({
  description: `
  List potential members
A paginated list of the users who can potentially be added to a
collaboration
in the given context.

For courses, this consists of all enrolled users.  For groups, it is
comprised of the
group members plus the admins of the course containing the group.
    `,
  parameters: listPotentialMembersCoursesDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListPotentialMembersCoursesData, "url"> ) => {
    try {
      const { data } = await listPotentialMembersCourses(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    