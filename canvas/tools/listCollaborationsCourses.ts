
import { tool } from "ai";
import { listCollaborationsCoursesDataSchema } from "./aitm.schema.ts";
import { listCollaborationsCourses, ListCollaborationsCoursesData } from "..";

export default tool({
  description: `
  List collaborations
A paginated list of collaborations the current user has access to in the
context
of the course provided in the url. NOTE: this only returns
ExternalToolCollaboration type
collaborations.

curl https://<canvas>/api/v1/courses/1/collaborations/
    `,
  parameters: listCollaborationsCoursesDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListCollaborationsCoursesData, "url"> ) => {
    try {
      const { data } = await listCollaborationsCourses(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    