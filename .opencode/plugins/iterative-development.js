/**
 * iterative-development plugin for OpenCode.
 *
 * Registers the bundled skills directory so OpenCode can discover this skill pack
 * when installed from the git package.
 */

import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

export const IterativeDevelopmentPlugin = async () => {
  const iterativeDevelopmentSkillsDir = path.resolve(__dirname, '../../skills');

  return {
    config: async (config) => {
      config.skills = config.skills || {};
      config.skills.paths = config.skills.paths || [];

      if (!config.skills.paths.includes(iterativeDevelopmentSkillsDir)) {
        config.skills.paths.push(iterativeDevelopmentSkillsDir);
      }
    }
  };
};
