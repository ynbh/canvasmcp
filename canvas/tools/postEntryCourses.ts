
import { tool } from "ai";
import { postEntryCoursesDataSchema } from "./aitm.schema.ts";
import { postEntryCourses, PostEntryCoursesData } from "..";

export default tool({
  description: `
  Post an entry
Create a new entry in a discussion topic. Returns a json representation of
the created
entry (see documentation for 'entries' method) on success.
    `,
  parameters: postEntryCoursesDataSchema.omit({ url: true }),
  execute: async (args : Omit<PostEntryCoursesData, "url"> ) => {
    try {
      const { data } = await postEntryCourses(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    