
import { tool } from "ai";
import { listAllFoldersCoursesDataSchema } from "./aitm.schema.ts";
import { listAllFoldersCourses, ListAllFoldersCoursesData } from "..";

export default tool({
  description: `
  List all folders
Returns the paginated list of all folders for the given context. This will
be
returned as a flat list containing all subfolders as well.
    `,
  parameters: listAllFoldersCoursesDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListAllFoldersCoursesData, "url"> ) => {
    try {
      console.log(args)
      const { data } = await listAllFoldersCourses(args);
      console.log(data)
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    