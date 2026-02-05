import { describe, it, expect } from 'vitest'
import { NODE_COLORS } from '../../src/main'

describe('Theme Configuration', () => {
    it('should have the correct color for project nodes', () => {
        expect(NODE_COLORS.project).toBe('#ff2e63')
    })

    it('should have a matrix green color for guidelines', () => {
        expect(NODE_COLORS.guideline).toBe('#00ff9d')
    })

    it('should contain all required node types', () => {
        const requiredTypes = ['project', 'concept', 'rule', 'guideline', 'instruction', 'resource', 'test', 'default']
        requiredTypes.forEach(type => {
            expect(NODE_COLORS).toHaveProperty(type)
        })
    })
})
