
import { tool } from "ai";
import { resolvePathCoursesFullPathDataSchema } from "./aitm.schema.ts";
import { resolvePathCoursesFullPath, ResolvePathCoursesFullPathData } from "..";

export default tool({
  description: `
  Resolve path
Given the full path to a folder, returns a list of all Folders in the path
hierarchy,
starting at the root folder, and ending at the requested folder. The given path
is
relative to the context's root folder and does not include the root folder's name
(e.g., "course
files"). If an empty path is given, the context's root folder alone
is returned. Otherwise, if no
folder exists with the given full path, a Not Found
error is returned.
    `,
  parameters: resolvePathCoursesFullPathDataSchema.omit({ url: true }),
  execute: async (args : Omit<ResolvePathCoursesFullPathData, "url"> ) => {
    try {
      const { data } = await resolvePathCoursesFullPath(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    